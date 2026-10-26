from .db import Repository, execute
from .allocation import validate

class BucketRepo(Repository):
    table, columns = "buckets", ("label", "percent")

    def save_percents(self, percents):
        """percents: {bucket_id: float}. Validated, then written in one commit."""
        validate(list(percents.values()))
        execute("UPDATE buckets SET percent=? WHERE id=?", rows=[(p, i) for i, p in percents.items()])

buckets = BucketRepo()
