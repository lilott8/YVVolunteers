import sys
import logging
from cli import CLI
import volunteers as v


def main(args: str):
    logger = logging.getLogger(__name__)
    config = CLI().build_config(args)
    volunteers = v.Volunteers(config).build_volunteers()
    heuristic = config.heuristic.get_strategy(config.group_size)
    groups = heuristic.build_groups(volunteers)
    if config.output:
        with open("{}/output.json".format(config.output), 'w') as f:
            f.write(groups)
    else:
        logger.warning(groups)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:\t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s')
    main(sys.argv[1:])
