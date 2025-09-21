
# GitDash: A Data-Driven Dashboard for Monitoring Team Progress in Software Engineering Education

GitDash is a data-informed dashboard designed to visualize and assess student engagement in software engineering team
projects. By synthesizing GitHub activity data and peer evaluation scores, GitDash provides instructors with an integrated platform to explore contribution patterns, detect imbalances in participation, and interpret team dynamics across collaboration, commitment, and conflict.

The system employs Principal Component Analysis (PCA) and K-means clustering to classify teams into behavioral archetypes, enhancing interpretability and enabling targeted instructional support. Through interactive panels focusing on weekly activity, team trends, and individual member insights GitDash facilitates real-time monitoring and supports equitable, evidence-based assessment practices. The tool demonstrates how combining behavioral and perceptual data can inform pedagogy and foster more transparent evaluation in collaborative software education.

# Research

GitDash was introduced in the paper:

"GitDash: A Data-Driven Dashboard for Monitoring Team Progress in Software Engineering Education" by Rahul Bijoor and Kevin Buffardi

to be published and presented at [Consortium for Computing Sciences in Colleges, Northwestern Regional Conference](CCSC-NW '25).

Citation:

> To be determined (currently in press)

## Getting Started

Requirements:

* Python 3

### Install Dependencies

Before launching the dashboard, install dependencies:

```
pip install -r requirements.txt
```

### Launch Dashboard

```
streamlit run dashb.py
```

#