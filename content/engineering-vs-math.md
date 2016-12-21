Title: Engineering vs Math: Messiness in the system
Date: 2016-07-18 9:30
Tags: engineering, optimization, constraints, robustness
Status: published

Yesterday I went to [Lowes](http://www.lowes.com/) with my wife to get pieces for a [modular shelving unit](http://www.rubbermaid.com/en-US/shop-products/closet---shelving) we were installing in our laundry room.  Instead of going with a pre-packaged shelving arrangement, we had decided to custom cut the shelving for a better fit.  The store had several length options available for the main shelves: 12 foot, 6 foot, 4 foot, 3 foot.  I knew the length of each of the 6 pieces I needed, down to the quarter of an inch.  The store provided the service of cutting the stock shelve pieces to length for free.

At this point any readers who spent time in a linear optimization or operations research course may be starting to sweat a little bit.  If you're not sure why, it's because what I just mentioned is a version of something usually referred to as "the cutting stock problem", and this can be expressed as [a well formed mathematical problem](http://www4.ncsu.edu/~kksivara/ma505/handouts/gilmore-gomory2.pdf) with a definite optimal solution.  Since you took the class, you **should** know [how to solve it](https://en.wikipedia.org/wiki/Simplex_algorithm), and if you don't, then well I guess math's not your thing after all right?

![No math](https://cdn.meme.am/instances/500x/66238928.jpg)

Hmmm.  Or at least that was the feeling that I had while I was standing in the aisle yesterday trying to figure this thing out.  Unfortunately, from my class in linear optimization I also remembered that:

1. Actually expressing a real world problem as a system of linear equations can be pretty tough
2. After that, you usually wanted a computer for solving anything with more than ~3 simultaneous equations
3. You'd still need to program the computer for the algorithm, or find a package to do it for you

At this point I realized the math side of my brain was failing me and I had to figure out a different approach to the problem.  That or my wife came by and asked why it was taking so long.  It's hard to keep track of those kinds of details.  So I just picked "the dumb solution" (use a couple of 12 foot long shelves) and asked to have someone paged over to cut the shelves for us.

Having now been shaken out of my mathematical stupor, I realized a few other details that I had missed in my singular pursuit of a mathematically elegant solution to my problem:

1. Several of the long shelve stock pieces were bent. So we were probably going to get them for a discount.  (We ended up getting them for half price.)
2. For the pieces that were bent, I had to rearrange the cuts to work around the bent pieces of the shelve, so having a little waste (i.e. slack) was necessary.
3. The shelve stock pieces were $20 each for 12 foot sections, but the mounting hardware packs were $12 and corner pieces were $18. So the price of straight shelve pieces was going to be only a small part of the total price. (It ended up being $20 of a $180 total.)
4. The waste pieces weren't really waste, since I could use them as a [makeshift trellis](https://www.youtube.com/watch?v=2YDe08UQop0) in our garden.

So really my focus on the math had caused me to ignore a lot of pretty obvious factors that were much more important than setting up the exact arrangement of cuts to mimimize waste.

There are parallels good practices in software here.  Something about [measuring before optimizing](http://www.catb.org/esr/writings/taoup/html/ch12s02.html).  There are parallels to good engineering here.  Something about [being explicit about your assumptions](https://en.wikipedia.org/wiki/Assumption-based_planning).  The funny thing is that these relatively easy to remember heuristics will often get you closer to a globally optimal and robust solution than focusing on the parts of the system that are well behaved and expressible in clear mathematical terms.

Hopefully this can be as good of a reminder for some of you as it was for me.

---

P.S. - 
I had to go back and use my hacksaw to trim some of those cut pieces anyway. It turns out my measurements were good but the shelves were designed to have 1/4-1/2 inch of space between them.  That and the corners of the laundry room were not perfectly square.
