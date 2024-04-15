import os

from argparse import ArgumentParser
from pathlib import Path
from sys import argv

def main(args):
    arg_p = ArgumentParser('python gen_results.py', description='Generates TREC_EVAL results file')
    arg_p.add_argument('-m', '--metrics', type=str, default=None, help='Comma-separated metric list (e.g. \'degree,eigenvector,betweenness\').')
    arg_p.add_argument('-r', '--reverse', action='store_true', help='Revert the relevance order')

    args = arg_p.parse_args(args[1:])

    metrics = args.metrics
    if metrics is None:
        print('No metrics provided.')
        exit(1)

    metrics = metrics.split(',')

    reverseSort = args.reverse

    for metric in metrics:
        output_filename = f'{metric}.results.test'
        open(output_filename, 'w').close() # Clean if exists
        
        with open(output_filename, 'a') as out:
            dirs = [d[0] for d in os.walk("..")]
            for d in sorted(dirs):
                if d == '..' or d == '../eval' or d == '../eval/plots':
                    continue

                queryid = Path(d).stem
                metric_recs_file = os.path.join(d, f'{metric}.txt')
                with open(metric_recs_file, 'r') as f:
                    if reverseSort:
                        f = reverse(list(f))

                    rank = 0
                    score = 8808 # num. of nodes in the catalog
                    for line in f:
                        contents = line.strip().split()
                        documentid = contents[0]

                        rank += 1
                        score -= 1
                        out_line = f'{queryid} Q0 {documentid} {rank} {score} {metric.upper()}'
                        out.write(f'{out_line}\n')
                        print(out_line)

if __name__ == '__main__':
    exit(main(argv))

