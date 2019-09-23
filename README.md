# WAF-A-MoLE

A *guided mutation-based fuzzer* for ML-based Web Application Firewalls, inspired by AFL and based on the excellent [FuzzingBook](https://www.fuzzingbook.org) from Andreas Zeller et al.
Given an input SQL injection query, it tries to produce a *semantics-invariant* query that is able to bypass the target WAF.
You can use this tool for assesting the robustness of your product by letting WAF-A-MoLE exploring the space of solution to find dangerous "blind spots" left uncovered by the target classifier.


[![Python Version](https://img.shields.io/badge/Python-3.7-green.svg)](https://www.python.org/downloads/release/python-374/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/AvalZ/WAF-A-MoLE/blob/master/LICENSE)

# Architecture

![WAF-A-MoLE Architecture](docs/fig/WAF-A-MoLE.png)

WAF-A-MoLE takes an initial payload and inserts it in the payload **Pool**, which manages a priority queue ordered on the WAF confidence score over each payload.

During each iteration, the head of the payload Pool is passed to the **Fuzzer** and it is randomly mutated, applying one of the available mutation operators.


## Mutation operators

Mutations operators are all *semantics preserving* and they leverage the flexibility of the SQL language (in this version, MySQL).

These are the mutation operators available in the current version of WAF-A-MoLE.

| Mutation | Example | 
| --- | --- |
|  Case Swapping | `admin' OR 1=1#` ⇒ `admin' oR 1=1#` |
| Whitespace Substitution | `admin' OR 1=1#` ⇒ `admin'\t\rOR\n1=1#`| 
| Comment Injection | `admin' OR 1=1#` ⇒ `admin'/**/OR 1=1#`|
| Comment Rewriting | `admin'/**/OR 1=1#` ⇒ `admin'/*xyz*/OR 1=1#abc`|
| Integer Encoding | `admin' OR 1=1#` ⇒ `admin' OR 0x1=(SELECT 1)#`| 
| Operator Swapping | `admin' OR 1=1#` ⇒ `admin' OR 1 LIKE 1#`| 
| Logical Invariant | `admin' OR 1=1#` ⇒ `admin' OR 1=1 AND 0<1#`| 


# Running WAF-A-MoLE

## Prerequisites

* [numpy](https://numpy.org/)
* [keras](https://keras.io/)
* [scikit-learn](https://scikit-learn.org/stable/)
* [joblib](https://github.com/joblib/joblib)
* [sqlparse](https://github.com/andialbrecht/sqlparse)
* [networkx](https://networkx.github.io/)
* [Click](https://click.palletsprojects.com/en/7.x/)

## Setup

`pip install -r requirements.txt`

## Sample Usage

You can evaluate the robustness of your own WAF, or try WAF-A-MoLE against some example classifiers.
In the first case, have a look at the [Model](https://github.com/AvalZ/waf-a-mole/blob/master/wafamole/models/model.py) class. Your custom model need to implement this class in order to be evaluated by WAF-A-MoLE.
We already provide wrappers for *sci-kit learn* and *keras* classifiers that can be extend to fit your feature extraction phase (if any).

### Help

`wafamole --help` 


### Evading example models

We provide some pre-trained model you can have fun with, located in [wafamole/models/custom/example_models](https://github.com/AvalZ/waf-a-mole/tree/master/wafamole/models/custom/example_models).
The classifiers we used are listed in the table below.

| Classifier name| Algorithm
| --- | --- |
| [WafBrain](https://github.com/BBVA/waf-brain) | Recurrent Neural Network| 
| Token-based | Naive Bayes | 
| Token-based | Random Forest | 
| Token-based | Linear SVM | 
| Token-based | Gaussian SVM | 
| [SQLiGoT](https://www.sciencedirect.com/science/article/pii/S0167404816300451) - Directed Proportional | Gaussian SVM | 
| [SQLiGoT](https://www.sciencedirect.com/science/article/pii/S0167404816300451) - Directed Unproportional | Gaussian SVM |
| [SQLiGoT](https://www.sciencedirect.com/science/article/pii/S0167404816300451) - Undirected Proportional | Gaussian SVM |
| [SQLiGoT](https://www.sciencedirect.com/science/article/pii/S0167404816300451) - Undirected Unproportional | Gaussian SVM |


#### Token-based - Naive Bayes

Bypass the pre-trained token-based Naive Bayes classifier using a `admin' OR 1=1#` equivalent.

```bash
wafamole evade --model-type token wafamole/models/custom/example_models/nb_trained.dump  "admin' OR 1=1#"
```

#### Token-based - Random Forest

Bypass the pre-trained token-based Random Forest classifier using a `admin' OR 1=1#` equivalent.

```bash
wafamole evade --model-type token wafamole/models/custom/example_models/rf_trained.dump  "admin' OR 1=1#"
```

#### Token-based - Linear SVM

Bypass the pre-trained token-based Linear SVM classifier using a `admin' OR 1=1#` equivalent.

```bash
wafamole evade --model-type token wafamole/models/custom/example_models/lin_svm_trained.dump  "admin' OR 1=1#"
```

#### Token-based - Gaussian SVM

Bypass the pre-trained token-based Gaussian SVM classifier using a `admin' OR 1=1#` equivalent.

```bash
wafamole evade --model-type token wafamole/models/custom/example_models/gauss_svm_trained.dump  "admin' OR 1=1#"
```

#### SQLiGoT

Bypass the pre-trained SQLiGOT classifier using a `admin' OR 1=1#` equivalent.
Use **DP**, **UP**, **DU**, or **UU** for (respectivly) Directed Proportional, Undirected Proportional, Directed Unproportional and Undirected Unproportional.

```bash
wafamole evade --model-type DP wafamole/models/custom/example_models/graph_directed_proportional_sqligot "admin' OR 1=1#"
```

**BEFORE LAUNCHING EVALUATION ON SQLiGoT**
This classifier is really strong, since the feature extraction phase produce vectors with structure and the pre-trained classifiers are strongly regularized.
It may take a long time (up to 3 hours) for some variants (see Benchmark section) to produce a payload that achieves evasion.

# Benchmark

# Contribute

