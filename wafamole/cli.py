import click
import pickle
import re
from wafamole.evasion import EvasionEngine
from wafamole.evasion.random import RandomEvasionEngine
from wafamole.exceptions.models_exceptions import UnknownModelError
from wafamole.models import TokenClassifierWrapper, WafBrainWrapper, SQLiGoTWrapper, MLBasedWAFWrapper
try:
    from wafamole.models.modsec_wrapper import PyModSecurityWrapper
except ImportError:
    # ModSecurity module is not available
    pass

@click.group()
def wafamole():
    pass


@wafamole.command()
@click.option("--model-type", "-T", default="token", help="Type of classifier to load")
@click.option("--timeout", "-t", default=14400, help="Timeout when evading the model")
@click.option(
    "--max-rounds", "-r", default=1000, help="Maximum number of fuzzing rounds. Default: 1000"
)
@click.option(
    "--round-size",
    "-s",
    default=20,
    help="Fuzzing step size for each round (parallel fuzzing steps). Default: 20",
)
@click.option(
    "--threshold", default=0.5, help="Classification threshold of the target WAF [0.5]"
)
@click.option(
    "--random-engine",
    default=None,
    help="Use random transformations instead of evolution engine. Set the number of trials",
)
@click.option(
    "--output-path",
    default=None,
    help="Location were to save the results of the random engine. NOT USED WITH REGULAR EVOLUTION ENGINE",
)
@click.argument("model-path", default="")
@click.argument("payload")
def evade(
    model_path,
    model_type,
    payload,
    max_rounds,
    round_size,
    timeout,
    threshold,
    random_engine,
    output_path
):
    if model_type == "token":
        model = TokenClassifierWrapper().load(model_path)
    elif model_type == "mlbasedwaf":
        model = MLBasedWAFWrapper().load(model_path)
    elif model_type == "UU":
        model = SQLiGoTWrapper(undirected=True, proportional=False).load(model_path)
    elif model_type == "UP":
        model = SQLiGoTWrapper(undirected=True, proportional=True).load(model_path)
    elif model_type == "DU":
        model = SQLiGoTWrapper(undirected=False, proportional=False).load(model_path)
    elif model_type == "DP":
        model = SQLiGoTWrapper(undirected=False, proportional=True).load(model_path)
    elif model_type == "waf-brain":
        model = WafBrainWrapper(model_path)
    elif re.match(r"modsecurity_pl[1-4]", model_type):
        pl = int(model_type[-1])
        try:
            model = PyModSecurityWrapper(model_path, pl)
        except Exception:
            print("ModSecurity wrapper is not installed, see https://github.com/AvalZ/pymodsecurity to install")
            exit()
    else:
        raise UnknownModelError("Unsupported model type")

    engine = RandomEvasionEngine(model) if random_engine is not None else EvasionEngine(model)
    query_body = payload
    if random_engine is not None:
        random_results = []
        for i in range(int(random_engine)):
            engine.evaluate(query_body, max_rounds, 1, timeout, threshold)
            random_results.append(engine.transformations)
            print("Round {} done".format(i))
        if output_path is not None:
            with open(output_path, 'wb') as out_file:
                pickle.dump(random_results, out_file)
    else:
        engine.evaluate(query_body, max_rounds, round_size, timeout, threshold)
