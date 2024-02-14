import streamlit as st
from matplotlib import pyplot as plt
import numpy as np


@st.experimental_memo
def get_numbers():
    sets = []
    for i in range(10):
        sets.append(np.random.normal(1, 1, size=100))
    return sets


sets = get_numbers()


@st.experimental_memo
def get_plot(i):
    fig, ax = plt.subplots()
    ax.hist(sets[i], bins=20)
    return fig


# create a bunch of figures
figs = [get_plot(i) for i in range(10)]

# with st.expander('Using a slider'):

#   plot = st.container()

# use st.slider to select
#  index = st.slider('figure index', 1, 10)

# use st.pyplot
# with plot:
#    st.pyplot(figs[index-1])

with st.expander('Using tabs'):
    tabs = st.tabs(list(np.array(range(1, 11)).astype(str)))

    for i in range(10):
        tabs[i].pyplot(figs[i])
