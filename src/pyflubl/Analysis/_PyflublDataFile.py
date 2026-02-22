def load_bookkeeping(file_name) :
    import json
    with open(file_name, "r") as f :
        bookkeeping = json.load(f)
    return bookkeeping