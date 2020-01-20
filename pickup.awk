BEGIN { print "[" }
{
  n = split($1, a, "-")
  print "    {"
  print "      'level': " a[1] ","
  print "      'odds': ["
  for (i = 2; i <= NF; ++i) { f = $i; print "        (" percents[i] ", '" f "')," }
  print "      ]\n    },"
}
END { print "  ]," }
