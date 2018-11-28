#!/bin/bash

py.test --cov-report html:htmlcov --cov=docknv $@
