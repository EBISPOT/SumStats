"""
Applies a search and traversal on the datasets.
It is agnostic as to what sort of dataset we are traversing for what query we are performing.
"""

from sumstats.utils import utils
from sumstats.common_constants import *
import logging
from sumstats.utils import register_logger

logger = logging.getLogger(__name__)
register_logger.register(__name__)


def general_search(search_obj, max_size, arguments, restriction_dictionary=None):
    """
    :param search_obj: an object that has a 'query' method and that will perform the actual query
    :param max_size: the max size of the datasets that we are traversing/querying
    :param arguments: the arguments to be passed to the query
    :param restriction_dictionary: a dictonary of restriction objects (see sumstats.utils.restrictions)
    that will be applied to the datasets returned by the query
    :return: a tuple (datasets, index_marker) where 'datasets' is a dictionary with the names of the datasets and
    the data to be returned (the result of the query after applying restrictions) and index_marker is an integer indicating
    up to where the query went in the dataset so that the next query can calculate it's next start base on the index_marker.
    The index marker is needed as we are applying filtering (restrictions) to the data and the start/end size used in a query might
    not be the real indicators of up-till where we have been in the dataset.
    """
    iteration_size = search_obj.size
    logger.info("Searching with searcher %s, arguments %s, restrictions %s", str(search_obj.__class__), str(arguments),
                str(restriction_dictionary))

    while True:
        logger.debug("Searching for searcher %s with start %s and iteration size %s", str(search_obj.__class__),
                     str(search_obj.start), str(iteration_size))
        arguments['size'] = iteration_size
        arguments['start'] = search_obj.start

        # call the query function
        search_obj.service.query(**arguments)

        result_before_filtering = search_obj.service.get_result()

        if _traversed(start=search_obj.start, result=result_before_filtering, max_size=max_size):
            break

        search_obj.index_marker = _increase_search_index(index_marker=search_obj.index_marker, start=search_obj.start,
                                                         iteration_size=iteration_size, max_size=max_size,
                                                         result=result_before_filtering)

        # after search index is increased, we can apply restrictions
        search_obj.service.apply_restrictions(**restriction_dictionary)

        search_obj.datasets = utils.extend_dsets_with_subset(search_obj.datasets, search_obj.service.get_result())
        search_obj.start = search_obj.start + iteration_size
        iteration_size = _next_iteration_size(size=search_obj.size, datasets=search_obj.datasets)

        if _search_complete(size=search_obj.size, datasets=search_obj.datasets):
            break

    logger.debug("Search for searcher %s completed. Returning index marker %s", str(search_obj.__class__),
                 str(search_obj.index_marker))
    search_obj.service.close_file()
    return search_obj.datasets, search_obj.index_marker


def _traversed(start, result, max_size):
    return (len(result[REFERENCE_DSET]) == 0) and (start >= max_size)


def _increase_search_index(index_marker, start, iteration_size, max_size, result):
    if (start + iteration_size) >= max_size:
        # will not search again, we have reached the end of the current group
        return index_marker + min(iteration_size, len(result[REFERENCE_DSET]))
    return index_marker + iteration_size


def _next_iteration_size(size, datasets):
    return size - len(datasets[REFERENCE_DSET])


def _search_complete(size, datasets):
    return len(datasets[REFERENCE_DSET]) >= size