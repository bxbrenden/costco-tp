#  costco-tp
A docker container for checking Costco's toilet paper stock


## Requirements
You must have the following things installed and working:
- docker


## Usage
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


## Building
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
