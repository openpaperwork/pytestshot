#!/bin/sh

rm -f $(find . -name \*_diff.png)
rm -f $(find . -name \*_out.png)
rm -f $(find . -name \*_diff_txt.png)

rm -f paperwork.conf
rm -rf data
rm -rf tmp
