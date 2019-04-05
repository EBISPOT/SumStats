toload_dir = config["tsvfiles_path"]
loaded_dir = config["loaded_files_path"]
h5dir = config["h5files_path"] + "/" + config["study_dir"]
STUDIES, = glob_wildcards(toload_dir + "/{ss_file}.tsv")

def get_filename(file):
    return file.split("/")[-1].split(".")[0]

def extract_ids_from_name(file):
    filename = get_filename(file)
    parts = filename.split('-')
    return parts


rule all:
    input:
        expand("{loaded_dir}/{ss_file}.tsv", loaded_dir=loaded_dir, ss_file=STUDIES)


rule write_to_hdf:
    input:
        tsv=toload_dir + "/{ss_file}.tsv"
    output:
        hdf=h5dir + "/file_{ss_file}.h5"
    params:
        mem=10000
    shell:
        "filename=$(basename {input.tsv}); "
        "name=$(echo $filename | cut -f 1 -d '.'); "
        "study=$(echo $name | cut -d'-' -f2); "
        "trait=$(echo $name | cut -d'-' -f3); "
        "echo {input.tsv}; "
        "echo $study; "
        "gwas-load -f $filename -study $study -trait $trait"
        

rule cleanup:
    input:
        hdf= h5dir + "/file_{ss_file}.h5",
        tsv=toload_dir + "/{ss_file}.tsv"
    output:
        loaded_dir + "/{ss_file}.tsv"
    params:
        mem=1000,
        loaded_dir = loaded_dir
    shell:
        """
        mv {input.tsv} {params.loaded_dir}
        """

