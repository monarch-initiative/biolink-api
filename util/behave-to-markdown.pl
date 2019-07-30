#!/usr/bin/perl

my $BASE = "http://api.monarchinitiative.org/api";

print "This is a marked up version of the executable behave tests in the [tests](tests/) directory\n\n";

foreach my $f (@ARGV) {
    open(F,$f);
    while(<F>) {
        if (m@^ *Given a path@) {
            s@^ *Given a path "(.*)"@URL: [$BASE$1]($BASE$1)\n@;
        }
        elsif (m@Scenario:@) {
            s@^ *Scenario: (.*)@Scenario: __$1__\n@;
        }
        elsif (m@^ *when @) {
            s@^ *when @\nwhen @;
            s@$@:\n@;
        }
        elsif (m@^ *then @) {
            s@^(\s+)@ * @;
        }
        elsif (m@^ *and @) {
            s@^(\s+)@    * @;
        }
        elsif (m@^Feature: @) {
            s@^Feature: @# @;
        }

        if (m@JSON.*JSONPath@) {
            s@"@`@g;
        }
        
        print $_;
    }
    close(F);
    print "\n";
}
