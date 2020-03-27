#  costco-tp
A docker container for checking Costco's toilet paper stock


## Requirements
You must have the following things installed and working:
- docker


## Overview
This container is a python script that asynchronously checks all 11 of Costco's toilet paper / tissue product pages for stock.
It uses selenium webdriver to navigate to each page, set the zip code to the user's local one, waits for the page to refresh, and then reports back the stock status.
This process takes about 1-2 minutes to complete.

It uses a local file called `tp_urls.txt` which has the following format:

```
# ITEM_NAME<TWO SPACES>ITEM_URL
Cottonelle  https://www.costco.com/cottonelle-ultra-comfort-care-toilet-paper%2c-36-rolls.product.100465152.html
```


## Usage
Configure your zip code / postal code as the `$POSTAL_CODE` environment variable:

```bash
# Linux
export POSTAL_CODE='12345'
```

Start the container:
```bash
docker run --memory 2048mb --shm-size 2g -d bxbrenden/costco-tp:latest
```

Find out the container ID with:
```bash
docker ps
```

Watch the logs of the container for output:
```bash
docker logs --follow <CONTAINER_ID>
```

### Example Output:

```
charmin-ultrasoft: Out of Stock
windsoft: Out of Stock
kirkland-signature: Out of Stock
kleenex-tissue1: Out of Stock
charmin-ultrastrong: Out of Stock
quilted-northern: Out of Stock
kleenex-TP: Out of Stock
cottonelle: Out of Stock
scott: Out of Stock
kirkland-signature-ultrasoft: Out of Stock
kleenex-tissue2: Out of Stock
```


## Contributing
I don't accept PRs because this RAM hog of a container is just a toy project.
Please open an issue if you have a suggestion.
Otherwise, please feel free to fork this and modify as you see fit.


## Building
This section is just a note to self.

Clone the source:

```bash
git clone git@github.com:bxbrenden/costco-tp.git
```

Build the container (note the `.` at the end of the command):

```bash
docker build -t bxbrenden/costco-tp:<VERSION_TAG> .
```

Upload to DockerHub:

```bash
docker push bxbrenden/costco-tp:<VERSION_TAG>
```