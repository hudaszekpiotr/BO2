#!/usr/bin/python
# -*- coding: utf-8 -*-
from project_app import cli, __app_name__


def main():
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    main()
