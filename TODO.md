Question:
 - is networkx's .degree() correctly handling our weights?
   [x] no, it wasn't
   [ ] verify that Reid's definitions are correct
 - look at 2d histograms
 - normalize 2d histogram?
  -  by total size???
 - betweenness
 - clustering
   - triangles?
   - cl
 - simply look at Tunisia's degree over time
 
 - 
 
 - clustering
 - centrality
 - betweenness
 - 
 
 chi^2 or t??
[x]  -> scipy.stats.chisquare
[ ] 
[x] extract city
 [ ] verify that this is behaving itself; this looks strange:
```
 (('Cities', (2012, 2)), ['Sfax']),
 (('Cities', (2012, 12)), ['La Mannouba']),
 (('Cities', (2010, 6)), ['Sfax']),
 (('Cities', (2010, 7)), ['Monastir']),
 (('Cities', (2009, 7)), ['Monastir']),
 (('Cities', (2011, 12)), ['Gabes']),
 (('Cities', (2006, 3)), ['Monastir']),
 (('Cities', (2006, 6)), ['Tunis']),
 (('Cities', (2014, 9)), ['Tunis']),
 (('Cities', (2010, 4)), ['Sousse Tunisie', 'Sousse']),
 (('Cities', (2008, 3)), ['Sfax']),
 (('Cities', (2009, 4)), ['Tunis']),
 (('Cities', (2013, 5)), ['Sfax']),
 (('Cities', (2011, 2)), ['Sfax']),
 (('Cities', (2012, 3)), ['Tunis'])]
```

--------------

--> a bunch of series over time

------------

We want to know if the Arab Spring might have had an effect.
This comes down to testing whether time has a significant effect on any of the stats we measure.
*there is more than one way to test for significance*
1) (pearson's) chi-squared test: consider each month as a separate category and test if you can assume all are equal to their means
2) do a t-test
  --> the one sample t-test is essentially equivalent to the chi-squared
  ^ oh, a bug: the samples are not independent!!!! shit.
2b) use a t-test via OLS
 -> this is no good because it assumes a linear trend, which is super suspect in our data (in fact, we are explicitly expecting to see a dip in the middle and then a rise after
 we could add polynomial terms maybe. this option is open, but it's a lot of work to get it done over all possible graphs and check it properly
3) treat each month as a category and use a poisson model:
  this has the extra advantage
   --> test for joint significance, then investigate those further; *months* that are (t-test) significant are ones of interest; if the months immediately following the arab spring are significant then win
  this *still* has the problem of 
  .. I guess we can do just GoF and trust in that
  
  ah but most of our statistics are *not* counts. which makes this suspect.
   hm.
   shit.
  
  
4) use an autocorrelation statistic (sadly, the Durbin-Watson stat only does a test for one-step lag)