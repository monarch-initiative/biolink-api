#!/usr/bin/perl

my $BASE = "http://api.monarchinitiative.org/api";

foreach my $f (@ARGV) {
    open(F,$f);
    while(<F>) {
        s@Given a path "(.*)"@Given a path [$BASE$1]($BASE$1)@;
        print $_;
    }
    close(F);
}
