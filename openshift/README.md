# OpenShift Deployments

## Scrapers Deployment

First create the OpenShift secret containing the credentials for the scrapers:

```bash
$ oc process -f scrapers-secret.yml \
    -p TEIID_USER=<username> \
    -p TEIID_PASSWORD=<password> \
    -p NEO4j_USER=<username> \
    -p NEO4J_PASSWORD=<password> | oc create -f -
```

Then create the job that runs the initial scraping:

```bash
oc new-app scrapers.yml \
    -p NEO4J_SERVER=<fqdn> \
    -p CA_URL=<url> \
    -p SCRAPE_FROM_DAYS_AGO=<days>
```
