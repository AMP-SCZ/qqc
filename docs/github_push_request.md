# How to collaborate on Github updating a code


## Steps

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
12. Merge to a branch
13. Delete the branch
