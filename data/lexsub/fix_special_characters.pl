# This script takes in input an xml file (e.g. lexsub_trial.xml) and produces
# a second file (with extension .fixed) which removes spaces 
# in the representation of extended special characters
# between the number and the ; 
#
# We thank Richard Wicentowski and his student for spotting 
# this problem in the original corpus.

open IN, $ARGV[0];
open OUT, ">$ARGV[0].fixed";

while(<IN>)
{
	s/&#(\d+) ;/&#$1;/g;
	
	print OUT $_;
}

close IN;
close OUT;