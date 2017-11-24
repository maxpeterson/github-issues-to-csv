import csv

import requests


def auth_headers(token):
    return {
        'authorization': 'token {}'.format(token),
    }


def get_page_links(response):
    if 'link' not in response.headers:
        return {}

    # Parse links of the form '<LINK_URL1>; rel="LINK_REL1", <LINK_URL2>; rel="LINK_REL2"'
    links = [link.split(';') for link in response.headers['link'].split(',')]
    # Parse list of links (('<LINK_URL1>', ' rel="LINK_REL1"'), ('<LINK_URL2>', ' rel="LINK_REL2"'))
    return dict([
        (rel[6:-1], url[url.index('<') + 1:-1])
        for url, rel in links
    ])


def get_api(url, token, extra_headers=None, verbose=False):
    headers = auth_headers(token)

    if extra_headers is not None:
        headers.update(extra_headers)

    items = []
    next_url = url
    while True:
        if verbose:
            print('Getting {}'.format(next_url))
        response = requests.get(next_url, headers=headers)

        if not response.status_code == 200:
            raise Exception('status_code {} - {}'.format(response.status_code, response.text))

        item = response.json()
        if not isinstance(item, (list, tuple)):
            return item

        items.extend(item)

        pages = get_page_links(response)
        if 'next' not in pages:
            break

        next_url = pages['next']

    return items


def issue_to_row(issue):
    labels = [label['name'].encode('utf-8') for label in issue['labels']]

    points = next((l for l in labels if l.lower().find('points:') >- 1), '')\
        .split(':')[-1]\
        .strip()
    return [
        issue['number'],
        issue['title'].encode('utf-8'),
        issue['state'],
        points,
        issue['milestone'] and issue['milestone']['title'].encode('utf-8'),
        ', '.join(labels),
        issue['body'].encode('utf-8'),
        issue['html_url'],
        issue['created_at'],
        issue['updated_at'],
    ]


def project_to_row(project):
    return [
        project['id'],
        project['name'].encode('utf-8'),
        project['number'],
        project['state'],
        project['body'].encode('utf-8'),
        project['html_url'],
        project['created_at'],
        project['updated_at'],
    ]


def issues2csv(repo, token, outfile=None, verbose=False):
    api_url = 'https://api.github.com/repos/{}/issues'.format(repo)
    if outfile is None:
        outfile = '%s-issues.csv' % (repo.replace('/', '-'))

    items = get_api(api_url, token, verbose=verbose)

    with open(outfile, 'wb') as output:
        csvout = csv.writer(output)

        if verbose:
            print('Writing issues to {}'.format(outfile))

        csvout.writerow((
            'id',
            'Title',
            'State',
            'Points',
            'Milestone',
            'Labels',
            'Body',
            'URL',
            'Created At',
            'Updated At',
        ))

        for item in items:
            csvout.writerow(issue_to_row(item))


def projects2csv(repo, token, outfile=None, verbose=False):
    api_url = 'https://api.github.com/repos/{}/projects'.format(repo)
    headers = {'Accept': 'application/vnd.github.inertia-preview+json'}

    if outfile is None:
        outfile = '%s-projects.csv' % (repo.replace('/', '-'))

    items = get_api(api_url, token, extra_headers=headers, verbose=verbose)

    with open(outfile, 'wb') as output:
        csvout = csv.writer(output)

        if verbose:
            print('Writing issues to {}'.format(outfile))

        csvout.writerow((
            'id',
            'Name',
            'Number',
            'State',
            'Body',
            'URL',
            'Created At',
            'Updated At',
        ))

        for item in items:
            csvout.writerow(project_to_row(item))

def cards2csv(project, token,  outfile=None, verbose=False):
    api_url = 'https://api.github.com/projects/{}/columns'.format(project)
    headers = {'Accept': 'application/vnd.github.inertia-preview+json'}

    if outfile is None:
        outfile = 'project-{}-issues.csv'.format(project)

    columns = get_api(api_url, token, extra_headers=headers, verbose=verbose)

    with open(outfile, 'wb') as output:
        csvout = csv.writer(output)

        if verbose:
            print('Writing cards to {}'.format(outfile))

        csvout.writerow((
            'id',
            'Title',
            'Body',
            'State',
            'Points',
            'Milestone',
            'Labels',
            'URL',
            'Created At',
            'Updated At',
        ))

        for column in columns:
            cards_url = column['cards_url']
            cards = get_api(cards_url, token, extra_headers=headers, verbose=verbose)

            for card in cards:
                issue_url = card['content_url']

                if issue_url:
                    issue = get_api(issue_url, token, verbose=verbose)
                csvout.writerow(issue_to_row(issue))
