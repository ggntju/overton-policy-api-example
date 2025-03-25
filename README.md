# overton-policy-api-example

This is a simple example of how to use the Overton API.

Overton is a bridge connecting research with policy [Official Website](https://www.overton.io/about)

## Environment Setup

It is highly recommended to use a virtual environment to run this code, for example, I use `conda` to create a virtual environment.

```bash
conda create -n overton python=3.11
conda activate overton
```

Then install the dependencies. You can use `pip` to install the dependencies.

```bash
pip install -r requirements.txt
```

Or you can use `conda install` to install the dependencies.

```bash
conda install --file requirements.txt
```

Then copy the `.env.example` to `.env` and fill in the `OVERTON_API_KEY` with your key.

## Usage

Please refer to the `test.ipynb` for more details.

First, create a `user` object with the `query` string you want to search.

Then, call the `initialRequest` method to get the necessary information to start the search.

Next, call the `nextRequest` method to get the next page of results. It will write results of this page to the current directory if everything goes well. It will return a boolean value to indicate whether there is more data to be fetched. If it is `True`, then there is no more data to be fetched. If it is `False`, it means more data is available and you can call the `nextRequest` method again to get the next page of results OR it could also mean there is something wrong in the initial request.
