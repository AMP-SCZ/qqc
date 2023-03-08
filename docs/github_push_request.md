# How to collaborate on Github from another person's branch

## Contents

1. How to create a new pull request
2. How to make changes to another person's branch
3. How to suggest changes to another person's branch


## 1. How to create a new pull request

1. Pull the most recent version of the master branch

```sh
git pull
```


2. Branch out

```sh
git checkout -b newfunction_kcho
```

3.  Edit the code

4. Add and Commit

```sh
git add new_code.py
git commit -m "feat: new a_plus_one function is added"
```

5. Push to github

```sh
git push
```

6. Create push request
7. Request review and get comments
8. Pull any new changes added by collaborator

```sh
git pull
```

9. Edit the code locally
10. Commit and push the changes made

```sh
git add new_code.py
git commit -m "fix: removed unnecessary loop"
git push
```

11. Repeat 6 to 9 until no more concerns
12. Pull the most change from the branch that you're trying to merge into. (just in case others have changed the `master` branch)

```sh
git checkout master
git pull
git checkout newfunction_kcho
git merge master
```

14. Merge to a branch
15. Delete the branch




## 2. How to make changes to another person's branch

1. Checkout to another person's branch and pull the most recent changes.

```sh
git checkout another_branch
git pull
```

2.  Edit the code

3. Add and Commit

```sh
git add new_code.py
git commit -m "feat: new a_plus_one function is added"
```

4. Push to github

```sh
git push
```



## 3. How to suggest changes to another person's branch

1. Checkout to another person's branch and pull the most recent changes.

```sh
git checkout another_branch
git pull
```


2. Branch out

```sh
git checkout -b another_branch_suggestion
```

3.  Edit the code

4. Add and Commit

```sh
git add new_code.py
git commit -m "feat: new a_plus_one function is added"
```

5. Push to github

```sh
git push
```

6. Create push request
11. Repeat 6 to 9 of item 1 at the top until no more concerns
12. Pull the most change from the branch that you're trying to merge into. (just in case others have changed the `master` branch)

```sh
git checkout another_branch
git pull
git checkout another_branch_suggestion
git merge another_branch
```

14. Merge to a branch
15. Delete the branch
