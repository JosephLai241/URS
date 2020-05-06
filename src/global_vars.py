#===============================================================================
#                               Global Variables
#===============================================================================
import datetime as dt

### Get current date
date = dt.datetime.now().strftime("%m-%d-%Y")

### Scrape types
s_t = ["sub","user","comments"]

### Export options
eo = ["csv","json"]

### Illegal filename characters
illegal_chars = ["/","\\","?","%","*",":","|","<",">"]

### Subreddit categories
categories = ["Hot","New","Controversial","Top","Rising","Search"]
short_cat = [cat[0] for cat in categories]

### Confirm or deny options
options = ["y","n"]

### Convert UNIX time to readable format
def convert_time(object):
    return dt.datetime.fromtimestamp(object).strftime("%m-%d-%Y %H:%M:%S")