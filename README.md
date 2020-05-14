# Financial Web Crawler
Web Crawler for gathering financial news for scientific research purposes.

## Stack

The stack bellow was used mostly due to its ease of installation, configuration, and also efficiency and portability.
* Language: Python (3.7.4)
* Core crawler engine: Scrapy (1.8.0)

## Pre-installation

This system was developed in Ubuntu 16.04 but will work properly on any other Operational System(OS X, Windows, etc.).

However, this guide will only include instructions for plugins and packages that are not already installed on this OS. For this reason, we assume that technologies like a python interpreter and pipenv are ready for use, and should not be on the scope of this document.

* Now install pipenv dependency manager:

```bash

$ pip install --user pipenv

```

## Project configuration

Now we'll start setting up the project.

* Clone the repo from GitHub and change to project root directory.
After that, install project dependencies and go to python virtual env, by running:

```bash
$ pipenv install
$ pipenv shell
```

## Running the project

Now we will run the project and get query answers.

* The project will do the following actions:
    1. Download a raw data like a JSON or an HTML in a controlled not abusive manner, respecting instructions from `robots.txt` files
    2. Save data to a specific folder according to webpage source and stock or asset selected
    3. Parse the HTML or JSON and extract the data to a CSV file selecting only preselected fields
    

```bash
$ python scraper
```

* To run just the step **iii** above, pass the argument `--step=gen_csv`:

```bash
$ python scraper --step=gen_csv
```

* Only stocks present in the `companies_list.csv` are allowed to run if `--website=wsj_news`.
So if necessary, include new entries  in this file following previous entries as examples.

* Required params:

  `--crawl_type` allowed values: `api`, `website`
  
  `--stock` a single stock ticker present in the file `companies_list.csv`
  or the value `list` to run for all stocks in `companies_list.csv` 

* When no params are passed the default mode of this scraper runs a crawler with the following characteristics:
  
  `--website=wsj_news` for wall street journal API
  
  `--mode=default` default operation mode
  
  `--step=all` run all steps mentioned before
  
  `--max_requests=2` maximum number of consecutive requests
  
  `--max_elements=100` gets a maximum number of elements
  
  `--start_time` is the current time
  
  `--end_time` is unused as the systems defaults to the number maximum of consecutive requests


* Example to run with all possible fields:

```bash
$ python scraper --crawl_type=api --website=wsj_news --stock=btcusd --mode=default --step=all --max_requests=2 --end_time=2019-10-18T18:59:08 --start_time=2019-11-12T22:30:00
```

* Example to run greedy mode:

   >**Beware the greedy mode will run trough exhaustion and may lead to blockage if not used properly. This mode ignores `end_time` and `max_requests`, but it can consider `start_time`.**

```bash
$ python scraper --website=wsj_news --stock=btcusd --mode=greedy
```


## Further Improvements
   **Tests**

   Unitary and integration tests will guarantee consistency and good maintainability

   **Job scheduler**
   
   Adding a feature for scheduling each job separately with improve performance 

   **Work for any site**
   
   Right now the code only works for a specific news website, it will be adjusted for some other websites candidates:
   - Yahoo finance
    
   - Business Insider
    
   - News BTC
    
   - Be In Crypto
   
   **Design improvements**
    
   - It seem scrapy expects all loops in the same website are self-contained

   **Known issues**
    
   - See open issues in github
    

## Final considerations

* Go play around! =)
