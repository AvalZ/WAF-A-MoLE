"""
https://www.sciencedirect.com/science/article/pii/S0167404816300451
SQLiGoT: Detecting SQL injection attacks using graph of tokens and SVM

Implementation of graph SVM classifier
"""
import networkx as nx
import numpy as np
import re
import os
from sklearn.svm import SVC
import wafamole.tokenizer.allowed_tokens as alt
from wafamole.utils.check import type_check


def _histogram_of_tokens(tokens):
    total_length = len(alt.TOKENS)
    hist = [0 for _ in range(total_length)]
    for t in tokens:
        hist[alt.TOKENS.index(t)] = tokens.count(t)
    return hist


def _get_allowed_tokens():
    return alt.TOKENS


class SQLiGoT(SVC):
    """SQLiGoT implementation."""

    def __init__(
        self,
        C=100.0,
        kernel="rbf",
        degree=3,
        gamma=0.0774263682681127,
        coef0=0.0,
        shrinking=True,
        probability=True,
        tol=0.001,
        cache_size=200,
        class_weight=None,
        verbose=False,
        max_iter=-1,
        decision_function_shape="ovr",
        random_state=None,
        sliding_window_length=5,
    ):
        if sliding_window_length is None or type(sliding_window_length) != int:
            sliding_window_length = 5
        self._sliding_window_length = sliding_window_length
        super().__init__(
            C=C,
            kernel=kernel,
            degree=degree,
            gamma=gamma,
            coef0=coef0,
            shrinking=shrinking,
            probability=probability,
            tol=tol,
            cache_size=cache_size,
            class_weight=class_weight,
            verbose=verbose,
            max_iter=max_iter,
            decision_function_shape=decision_function_shape,
            random_state=random_state,
        )

    def _preprocess_input_query(self, query):
        query = query.strip().upper()
        query = re.sub(r"( |\t|\n|\r|/\*\*/|`)+", " ", query)
        query = alt.substitute_sysinfo(query, insert_space=True).strip()
        query = alt.apply_regexp(query, insert_space=True).strip()
        query = alt.substitute_punctation(query, insert_space=True).strip()
        query = re.sub(" +", " ", query).strip()
        query = alt.normalize_dots(query)
        splitted_string = query.split(" ")
        tokens = []
        for t in splitted_string:
            if t in _get_allowed_tokens():
                tokens.append(t)
            else:
                if len(t) > 1:
                    tokens.append("STR")
                else:
                    tokens.append("CHR")
        if "WHERE" not in tokens:
            return None
        tokens = tokens[tokens.index("WHERE") + 1 :]
        if not tokens:
            return None
        return tokens

    def _create_graph_from_sql_query(
        self, sql_query, proportional=False, undirected=False
    ):
        token_sequence = self._preprocess_input_query(sql_query)
        if token_sequence is None:
            return None
        graph = nx.Graph() if undirected else nx.DiGraph()
        token_count = _histogram_of_tokens(token_sequence)
        [
            graph.add_node(t, count=token_count[i])
            for i, t in enumerate(_get_allowed_tokens())
        ]
        for i, token in enumerate(token_sequence):
            stop_slide = (
                i + self._sliding_window_length
                if i + self._sliding_window_length < len(token_sequence)
                else len(token_sequence)
            )
            window = token_sequence[i + 1 : stop_slide]
            for j, slide_token in enumerate(window):
                additive_weight = (
                    i - j + self._sliding_window_length if proportional else 1
                )
                if graph.has_edge(token, slide_token):
                    graph[token][slide_token]["weight"] += additive_weight
                else:
                    graph.add_edge(token, slide_token, weight=additive_weight)
            if stop_slide == len(token_sequence):
                break
        return graph

    @staticmethod
    def _extract_feature_vector_from_directed_graph(graph, normalize=True):
        if not isinstance(graph, nx.DiGraph):
            raise ValueError()
        allowed = _get_allowed_tokens()
        in_degree_dict = [graph.in_degree(t, "weight") for t in allowed]
        max_in_degree = max(in_degree_dict) if normalize else 1
        out_degree_dict = [graph.out_degree(t, "weight") for t in allowed]
        max_out_degree = max(out_degree_dict) if normalize else 1
        if max_in_degree == 0 or max_out_degree == 0:
            return None
        feature_vector = []
        [
            feature_vector.extend((a / max_in_degree, b / max_out_degree))
            for (a, b) in zip(in_degree_dict, out_degree_dict)
        ]
        feature_vector = np.array(feature_vector)
        return feature_vector

    @staticmethod
    def _extract_feature_vector_from_undirected_graph(graph):
        if not isinstance(graph, nx.Graph):
            raise ValueError()
        allowed = _get_allowed_tokens()
        degree = [graph.degree(t, "weight") for t in allowed]
        max_degree = max(degree)
        count = [graph.node[t]["count"] for t in allowed]
        max_count = max(count)
        if max_count == 0 or max_degree == 0:
            return None
        feature_vector = []
        [
            feature_vector.extend((a / max_count, b / max_degree))
            for (a, b) in zip(count, degree)
        ]
        feature_vector = np.array(feature_vector)
        return feature_vector

    def preprocess_single_query(
        self, sql_query: str, undirected: bool = False, proportional: bool = True
    ):
        """Create feature vector from input query.
        
        Arguments:
            sql_query (str) : input sql query
        
        Keyword Arguments:
            undirected (bool) : create undirected graph if true (default: (False))
            proportional (bool) : create weighted graph if true (default: (True))

        Raises:
            TypeError: arguments are not typed correctly

        Returns:
            numpy ndarray : the feature vector extracted from the query
        """
        type_check(sql_query, str, "sql_query")
        type_check(undirected, bool, "undirected")
        type_check(proportional, bool, "proportional")

        graph = self._create_graph_from_sql_query(
            sql_query, proportional=proportional, undirected=undirected
        )
        if graph is None:
            return None
        extract_feat = (
            self._extract_feature_vector_from_undirected_graph
            if undirected
            else self._extract_feature_vector_from_directed_graph
        )
        feature_vector = extract_feat(graph)
        if feature_vector is None:
            return None
        return feature_vector

    def _create_feature_vectors_from_file(
        self, filepath, undirected=False, proportional=True, limit_samples=10000
    ):
        X = []
        with open(filepath, "r") as f:
            sql_queries = f.readlines()
        for i, sql_query in enumerate(sql_queries):
            if limit_samples is not None and i > limit_samples:
                break
            feature_vector = self.preprocess_single_query(
                sql_query, undirected=undirected, proportional=proportional
            )
            if feature_vector is None:
                if limit_samples is not None:
                    limit_samples += 1
                continue
            X.append(feature_vector)
        X = np.array(X)
        return X

    def _balance_data(self, X_a, X_b):
        max_lenght = min(len(X_a), len(X_b))
        X_a = X_a[:max_lenght]
        X_b = X_b[:max_lenght]
        return X_a, X_b

    def create_dataset(
        self,
        benign_filepath: str,
        sqlia_filepath: str,
        undirected=False,
        proportional=True,
        normalize=True,
        limit_samples=10000,
        balance=True,
        dump_to_file=True,
        check_cache=True,
        save_keyword_append="",
    ):
        """Create dataset of both sqli and sane queries, using the input paths.
        If check_cache is true, it tries to load previously computed dataset.
        
        Arguments:
            benign_filepath (str) : path to sane queries
            sqlia_filepath (str) : path to sqli queries

        Raises:
            TypeError: arguments are not typed correctly

        Keyword Arguments:
            undirected (bool) : true for undirected graphs (default: (False))
            proportional (bool) : true for weighted graphs (default: (True))
            normalize (bool) : true for normalizing weights of edges (default: (True))
            limit_samples (int) : if not None, how many queries per file to consider (default: (10000))
            balance (bool) : true for balancing the number of sane and sqli queries (default: (True))
            dump_to_file (bool) : true for storing the computed queries to file (default: (True))
            check_cache (bool) : enable dump load (default: (True))
            save_keyword_append (str) : append this string to both paths when saving results (default: (''))
        
        Returns:
            (numpy ndarray, numpy ndarray) : X and y
        """

        type_check(benign_filepath, str, "benign_path")
        type_check(undirected, bool, "undirected")
        type_check(proportional, bool, "proportional")
        type_check(normalize, bool, "normalize")
        type_check(balance, bool, "balance")
        type_check(dump_to_file, bool, "dump_to_file")
        type_check(save_keyword_append, str, "save_keyword_append")

        kind = "undirected" if undirected else "directed"
        prop = "proportional" if proportional else "unprop"
        if (
            check_cache
            and os.path.isfile(benign_filepath)
            and os.path.isfile(sqlia_filepath)
        ):
            X_benign = np.load(benign_filepath)
            X_sqlia = np.load(sqlia_filepath)
            if balance:
                X_benign, X_sqlia = self._balance_data(X_benign, X_sqlia)
            X = np.vstack((X_benign, X_sqlia))
            y = np.ones(len(X_benign) + len(X_sqlia))
            y[: len(X_benign)] = -1
            return X, y
        else:
            X_benign = self._create_feature_vectors_from_file(
                benign_filepath,
                undirected=undirected,
                proportional=proportional,
                normalize=normalize,
                limit_samples=limit_samples,
            )
            X_sqlia = self._create_feature_vectors_from_file(
                sqlia_filepath,
                undirected=undirected,
                proportional=proportional,
                normalize=normalize,
                limit_samples=limit_samples,
            )
        X_benign = np.unique(X_benign, axis=0)
        X_sqlia = np.unique(X_sqlia, axis=0)
        np.save(
            "{}graph_{}_{}_sane.npy".format(save_keyword_append, kind, prop), X_benign
        )
        np.save(
            "{}graph_{}_{}_sqlia.npy".format(save_keyword_append, kind, prop), X_sqlia
        )
        if balance:
            X_benign, X_sqlia = self._balance_data(X_benign, X_sqlia)
        X = np.vstack((X_benign, X_sqlia))
        y = np.ones(len(X_benign) + len(X_sqlia))
        y[: len(X_benign)] = -1
        return X, y
