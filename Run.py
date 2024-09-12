import pandas
import streamlit
import streamlit.web.cli as stcli
import sys
if __name__ == "__main__":
    sys.argv=["streamlit", "run", "init_parameters.py"]
    sys.exit(stcli.main())
