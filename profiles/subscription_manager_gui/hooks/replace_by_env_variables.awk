function repl_var(txt)
{
    evar = gensub(/.*%%(.*)\n.*/, "\\1", 1, txt)
    if (length(ENVIRON[evar]) > 0) {
        txt = gensub(/(.*)%%.*\n/, "\\1"ENVIRON[evar], 1, txt)
    }
    return txt
}

{
if (/%%.*%%/) {
replnum = 2
orig = $0
new = gensub(/%%/, "\n", replnum, orig);
while (orig != new) {
    orig = new
    new = repl_var(new)
    if (orig == new) {
        new = gensub(/(%%.*)\n/, "\\1%%", 1, new)
        orig = new
        replnum = replnum + 2
    }
    new = gensub(/%%/, "\n", replnum, new);
}
print new
next
}
print $0
}
