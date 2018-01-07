"""Start tests."""

import subprocess
subprocess.call(("py.test", "--cov-report", "html:htmlcov", "--cov=docknv"), shell=True)
subprocess.call(("start", "./htmlcov/index.html"), shell=True)
