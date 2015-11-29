import urllib2
import json
import argparse

# NOTE: Gerrit returns JSON with some leading magic characters, see
# http://gerrit-documentation.googlecode.com/svn/Documentation/2.5/rest-api.html#output


class Gerrit(object):

    def __init__(self, base_url=None):
        self.gerrit_url = base_url
        self.server = None

    def open_changes_url(self):
        return '%s/%s' % (self.gerrit_url, 'changes/?q=status:open')

    def change_detail_url(self, change_id):
        url_suffix = 'changes/%s/detail' % change_id
        return '%s/%s' % (self.gerrit_url, url_suffix)

    def get_response(self, specific_url):
        req = urllib2.Request(specific_url)
        req.add_header('Accept', 'application/json')
        res = urllib2.urlopen(req)
        s = res.read()
        all_changes = json.loads(s[5:])  # Skip leading magic characters
        return all_changes

    def is_ready_for_review(self, labels_json):
        return 'approved' not in labels_json['Code-Review'] and \
               'rejected' not in labels_json['Code-Review'] and \
               'value' not in labels_json['Code-Review']

    def is_reviewed(self, labels_json):
        return 'approved' in labels_json['Code-Review'] or \
               'rejected' in labels_json['Code-Review'] or \
               'value' in labels_json['Code-Review']

    def info_to_store(self, change_json):
        return change_json['subject']

    def all_open_changes(self):
        for_review = []
        reviewed = []
        all_changes = self.get_response(self.open_changes_url())
        for change_json in all_changes:
            detail = self.get_response(self.change_detail_url(change_json['id']))
            if self.is_ready_for_review(detail['labels']):
                for_review.append(self.info_to_store(change_json))
            elif self.is_reviewed(detail['labels']):
                reviewed.append(self.info_to_store(change_json))
        return (for_review, reviewed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get Gerrit status.')
    parser.add_argument('url')
    parser.add_argument('-c', '--change_id', required=False)
    args = parser.parse_args()

    changes = [args.change_id] if args.change_id else None
    g = Gerrit(base_url=args.url)

    (ready_for_review, reviewed) = g.all_open_changes()
    print
    print 'Ready for review:'
    for c in ready_for_review:
        print '', c
    print
    print 'Reviewed:'
    for c in reviewed:
        print '', c
    print
