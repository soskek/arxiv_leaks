# ArxivLeaks

Let's read hidden state of arxiv papers!

Most of papers on arxiv have latex files, which often contain much comment out. Dig up the valuable comments!

For example, you can extract a secret comment from "[Attention Is All You Need](https://arxiv.org/abs/1706.03762)", as below:
```
\\paragraph{Symbol Dropout} In the source and target embedding layers, we replace a random subset of the token ids with a sentinel id.  For the base model, we use a rate of $symbol\\_dropout\\_rate=0.1$.  Note that this applies only to the auto-regressive use of the target ids - not their use in the cross-entropy loss.
```
We can find "Symbol Dropout", which do not appear in the paper (pdf).


## Run

Feed text/page containing arxiv urls by `-t`.
```
python -u run.py -t deepmind.html -s arxiv_dir
```
To test, run `sh test.sh`. This pre-downloads a publication page of deepmind.

You can also read only selected papers by `-i`, feeding their arxiv ids.
```
python -u run.py -i 1709.04905 1706.03762 -s arxiv_dir
```

- `-s`: Downloaded arxiv pages and files are stored into this directory.
- `-o`: Output is printed and saved as a json file with this file path. Default is `./comments.json'.
