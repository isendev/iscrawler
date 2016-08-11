# iscrawler
Simple crawler to find LinkedIn profile URLs


## Assumptions/Caveats

* Parsing for <a> tags suffices...
 * a JS-rendered page would have a <noscript> section that leads to the static version
 * proper parsing can be accomplished with real page rendering e.g. with `webkit`
* a LinkedIn URL is itself a legitimate page into which to descend
* "Breadth-first" crawling suffices for a simple, efficient crawler
* Single process approach is sufficient at this point. 
  Given the scale of the task and unpredictabiility of 
  server response time, parallel crawling with multiple threads/machines 
  would be ideal. Celery is one possible choice in the next step to parallelization.
  
## Use

After downloading code, simply run:
`python crawl4urls.py`

The base URL is hardwired, for simplicity, as are some other parameters, but these could easily be made configurable.



