#!/usr/bin/env perl
use strict;
use warnings;
use File::Find;

# Mapping from hugo callout type -> GFM alert type
my %map = (
    info      => 'NOTE',
    warning   => 'WARNING',
    important => 'IMPORTANT',
);

sub transform {
    my ($text) = @_;

    $text =~ s{
        \{\{<\s*callout(?:\s+type=(\w+))?\s*>\}  # opening shortcode
        (.*?)                                    # body
        \{\{<\s*/callout\s*>\}\}                 # closing shortcode
    }{
        my $type = $1 // 'warning';
        my $hdr  = $map{lc $type} // uc($type);
        my $body = $2;
        $body =~ s/^/> /mg;
        "> [$hdr]\n$body"
    }egsx;

    return $text;
}

sub process_file {
    my ($file) = @_;
    return unless $file =~ /\.md$/i;

    local $/ = undef;
    open my $fh, '<', $file or die "Cannot open $file: $!";
    my $content = <$fh>;
    close $fh;

    my $new = transform($content);

    if ($new ne $content) {
        open my $out, '>', $file or die "Cannot write $file: $!";
        print $out $new;
        close $out;
        print "Transformed: $file\n";
    }
}

my $root = shift @ARGV // 'content';
find(
    {
        wanted   => sub { process_file($File::Find::name) if -f },
        no_chdir => 1,
    },
    $root
);
