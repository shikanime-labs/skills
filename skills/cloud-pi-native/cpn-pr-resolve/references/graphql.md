# GraphQL queries — cpn-pr-resolve

## list-threads

```bash
gh api graphql -f query='
  query($owner:String!,$repo:String!,$num:Int!) {
    repository(owner:$owner,name:$repo){
      pullRequest(number:$num){
        reviewThreads(first:100){
          nodes{
            id
            isResolved
            isOutdated
            comments(first:1){
              nodes{ body author{login} path line diffHunk }
            }
          }
        }
      }
    }
  }' -f owner=<org> -f repo=<repo> -F num=<M>
```

## reply-thread

Replies do NOT nest the input — flat `pullRequestReviewThreadId` + `body`:

```bash
gh api graphql -f query='
  mutation($tid:ID!,$body:String!){
    addPullRequestReviewThreadReply(input:{
      pullRequestReviewThreadId:$tid, body:$body
    }){ comment{ databaseId } }
  }' -f tid=<threadId> -F body=<reply>
```

A reply alone never closes the thread — always follow with `resolve-thread`.

## resolve-thread

```bash
gh api graphql -f query='
  mutation($id:ID!){
    resolveReviewThread(input:{threadId:$id}){ thread{isResolved} }
  }' -f id=<threadId>
```
