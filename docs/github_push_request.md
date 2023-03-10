# A short summary of steps required to collaborate with others on Github

For QQC development, we will use `pnldev` branch as the core branch to merge any of within PNL updates (new branches will be merged into `pnldev` branch). Before making any edits to QQC, please create a new branch from the `pnldev` branch and create a push request (PR) back to merge the changes back to `pnldev` for code review.

```sh
git clone https://github.com/AMP-SCZ/qqc
cd qqc
git checkout pnldev
git pull
git checkout pnldev_nick_new_api
... # edit code / add updates
git push --set-upstream origin pnldev_nick_new_api
```
Then create a push request (PR), following step 6-11 of [How to add a new function](#1-how-to-add-a-new-function) below.


## Git basics

1. [How to add a new function](#1-how-to-add-a-new-function)
2. [How to make changes to another person's branch](#2-how-to-make-changes-to-another-persons-branch)
3. [How to suggest changes to another person's branch](#3-how-to-suggest-changes-to-another-persons-branch)


## 1. How to add a new function

1. Pull the most recent version of the master branch

```sh
mkdir ~/tmp
cd tmp
git clone https://github.com/AMP-SCZ/qqc
cd qqc
```


2. Branch out to a new branch

```sh
git checkout -b new_function_kcho
```

3. Edit the code

4. Select the files updated with `git add` and commit changes

```sh
git add new_code.py  # if you edited the new_code.py
git commit -m "feat: new a_plus_one function is added"
```

5. Push to github

```sh
git push --set-upstream origin new_function_kcho
```

6. Create push request
![This is an image](images/Pasted_Image_3_8_23__6_34_PM.png)
![This is an image](images/Pasted_Image_3_8_23__6_41_PM.png)


7. Request review and get comments

![This is an image](images/Pasted_Image_3_8_23__6_47_PM.png)


8. Work on the comments (Edit the code following the suggestions)
```sh
# pull if anyone pushed changes to the branch
git pull
```

Edit the code then,
```sh
git add new_code.py
git commit -m "fix: removed unnecessary loop"
git push
```

9. Once the review process is completed, pull the most recent changes from the branch that you're trying to merge into. (just in case others have changed the `master` branch)

```sh
git checkout master
git pull
git checkout new_function_kcho
git merge master
git push
```

10. Merge to a branch
![This is an image](images/Pasted_Image_3_8_23__6_54_PM.png)
![This is an image](images/Pasted_Image_3_8_23__6_54_PM-2.png)


11. Delete the branch
![This is an image](images/Pasted_Image_3_8_23__6_55_PM.png)



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
git pull
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
