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


## Building
Clone the source:

```bash
git clone git@github.com:bxbrenden/costco-tp.git
```

Build the container (note the `.` at the end of the command):

```bash
docker build -t bxbrenden/costco-tp:<VERSION_TAG> .
```
