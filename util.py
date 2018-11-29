def get_file_extension(file_):
    print(file_)
    print("file name:", file_.filename)
    return file_.filename.split(".")[-1].lower()
