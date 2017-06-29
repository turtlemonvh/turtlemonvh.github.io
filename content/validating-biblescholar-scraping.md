Title: Validating BibleScholar Scraping
Date: 2017-01-02 14:00
Tags: python, scraping, biblescholar
Status: published

As with any data scraping tool, verifying correctness in BibleScholar's verse scraping utilities was pretty important.  After my first run through verses, here is what I was seeing between versions.  Note that this is before I added the ESV translation, which as you'll see below is the version with the largest differences to other translations.

```
$ wc -l *.tsv
   30926 HCSB.tsv
   31102 KJV.tsv
   30852 NIV.tsv
   92880 total
```

Hmmm.  Something smells fishy here.  I know that some versions chose to leave out some verses or split verses in different places, but a difference of 250 verses between NIV and KJV (which I know to be similar translations) looked to be beyond a normal standard of error.  To fix this, I took the following steps.

----

## Step 1: See where the differences are and fix bugs in the processing script

All the verses were stored in tsv format (`<translation> <book> <chapter> <verse #> <text>`).  To make the analysis quick, I just extracted the `<book> <chapter> <verse #>` parts of the line into a file I named `.verses` do I could use [diff](http://man7.org/linux/man-pages/man1/diff.1.html) to check for differences between what verses were included.  The commands to create these files and produce the diffs were as follows.

```bash
# Generate files like "<book> <chapter> <verse>"
cat NIV.tsv | awk -F"\t" '{print $2, $3, $4}' > NIV.verses
cat ESV.tsv | awk -F"\t" '{print $2, $3, $4}' > ESV.verses
cat HCSB.tsv | awk -F"\t" '{print $2, $3, $4}' > HCSB.verses

# Diff 2 versions
diff NIV.verses ESV.verses
```

My process I used was

1. Find a verse that was missing in 1 version and present in another
2. Try to figure out why (could just be a difference in versions, but usually was a parsing error)
3. Fix the script responsible for extracting verses from a page
4. Re-create the TSV files
5. Return to step 1 and repeat until no more unexplained diffs appear.

You can see the series of changes I made to the script in this [git diff](https://github.com/turtlemonvh/biblescholar/commit/b21bed269c7ae4a31853a03f2ff00caba02c1e1a).  In addition to fixing bugs that were causing some verses to be skipped, these changes also fix bugs where only parts of verses were included.

## Step 2: Validate remaining changes line by line

After these changes, the line count difference was much better.  Note that KJV and NIV now have exactly the same verses.

```
$ wc -l *.tsv
   31086 ESV.tsv
   31101 HCSB.tsv
   31102 KJV.tsv
   31102 NIV.tsv
  124391 total
```

However, there is we still see some differences when we look at individual diffs, and we want to make sure that all those changes are explained away as intended differences between the versions.

### Version comparison: NIV vs ESV

```
$ diff ESV.verses NIV.verses
(... a bunch of things complaining about naming of "Song of Solomon" book)
> Matthew 12 47
23720a23722
> Matthew 17 21
23736a23739
> Matthew 18 11
23929a23933
> Matthew 23 14
24475a24480
> Mark 7 16 
24577a24583
> Mark 9 44 
24578a24585
> Mark 9 46 
24659a24667
> Mark 11 26 
24846a24855
> Mark 15 28 
25678a25688
> Luke 17 36 
25942a25953
> Luke 23 17 
26203a26215
> John 5 4 
27201a27214
> Acts 8 37
27463a27477
> Acts 15 34
27762a27777
> Acts 24 7
27913a27929
> Acts 28 29
28344a28361
> Romans 16 24
30657d30673
< 3 John 1 15
```

The first major difference was for [the book that comes after Ecclesiastes and before Isaiah](https://en.wikipedia.org/wiki/Song_of_Songs).  HCSB, ESV, and KJV all call it "Song of Solomon" but NIV (and Wikipedia, apparently) calls it "Song of Songs".  So when comparing with NIV, all verses in that chapter were marked as different.  But since I was just checking that all chapters and verses were included and not verifying that book names were the same, once I saw that the actual verses in that book were the same between all the other translations (e.g. ESV vs HCSB) I ignored those lines in the diff.

After that, I validated that every verse marked as present in the NIV and not present in the ESV is supposed to be missing.  I checked each one, and for each the ESV mentions that that verse was intentionally left out in a footnote.

There was only 1 case where a verse was present in the ESV and NOT in the NIV ([3 John 1:15](https://www.biblegateway.com/passage/?search=3+John+1&version=ESV)).  In that case the content is pretty much the same between the 2 translations.  They just chose to split the final verse of the book at a different place.

For the remainder of the comparisons, I use the NIV as the standard because it had more verses than the HCSB.

### Version comparison: NIV vs HCSB

```
$ diff NIV.verses HCSB.verses
27477d27476
< Acts 15 34
29058d29056
< 2 Corinthians 13 14
30909a30908
> Revelation 12 18
```

Checking out these diffs, we find:

* NIV and HCSB *both* leave out [Acts 15:34](https://www.biblegateway.com/passage/?search=Acts+15&version=NIV), but NIV had a stub for the verse in the HTML.  The following is what the verses look like in the produced tsv files:

```
NIV Acts    15  33  After spending some time there, they were sent off by the believers with the blessing of peace  to return to those who had sent them.
NIV Acts    15  34  
NIV Acts    15  35  But Paul and Barnabas remained in Antioch, where they and many others taught and preached  the word of the Lord.
```

* HCSB leaves out [2 Corinthians 13:14](https://www.biblegateway.com/passage/?search=2+Corinthians+13&version=HCSB)
* NIV leaves out [Revelation 12:18](https://www.biblegateway.com/passage/?search=Revelation+12&version=HCSB)

So those look fine.

### Version comparison: NIV vs KJV

Finally, we compare KJV to NIV.

```
$ diff NIV.verses KJV.verses
(... aside from the Song of Solomon naming difference, no difference)
```

Nice!  The translations that originally started out with a 250 verse difference are now exactly the same.

## Step 3: Reindex the data

Since I already created tooling for this, this was pretty easy.

```
# Back up existing database
$ mv verses.bleve verses.bleve.bk

# Make a new one
# Reindexing took <30s per version, so after 2 minutes I had a brand new database
$ artifacts/biblescholar-darwin-amd64 index -d ../downloads/

# Test it out
$ bleve query verses.bleve "peace I give to you" -l 4
4491 matches, showing 1 through 4, took 13.866456ms
    1. John-14-27-HCSB (0.614247)
        Text
                “Peace I leave with you. My peace I give to you. I do not give to you as the world gives. Your heart must not be troubled or fearful.
    2. John-14-27-NIV (0.614247)
        Text
                Peace I leave with you; my peace I give you.  I do not give to you as the world gives. Do not let your hearts be troubled  and do not be afraid.
    3. John-14-27-ESV (0.601036)
        Text
                Peace I leave with you;  my peace I give to you. Not as the world gives do I give to you.  Let not your hearts be troubled, neither  let them be afraid.
    4. John-14-27-KJV (0.588642)
        Text
                Peace I leave with you, my peace I give unto you: not as the world giveth, give I unto you. Let not your heart be troubled, neither let it be afraid.
```

Not too bad.

## Step 4: Deploy updated application to Elastic Beanstalk App

To do this, all I had to do was make sure that `verses.bleve` was in [the `search` directory](https://github.com/turtlemonvh/biblescholar/tree/master/search) (the one with the Makefile) and run `make elbzip` to [create the application source bundle](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/applications-sourcebundle.html).  Then I went to my app's Elastic BeanStalk Dashboard page, clicked the "Upload and Deploy" button, and uploaded the zip file.  Once that was uploaded I just selected the new release package and clicked "Deploy" from the drop down menu.  A few minutes later, everything was deployed.

<img src="/images/updating-biblescholar-elb-dashboard.png" alt="Updating BibleScholar ELB Dashboard" style="width: 100%; display: block; margin: 0 auto; border: 1px solid; padding: 3px;"/>

Really, they make this stuff pretty simple.  I haven't even bothered using [the command line tools](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html) since the dashboard is so quick to work with.

----

And with that BibleScholar is now running with a more accurate record of scripture.  I hope this description of the processes was helpful - let me know in the comments below or find me [on twitter](https://twitter.com/turtlemonvh).

