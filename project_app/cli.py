#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Optional
import typer
from project_app import __app_name__, __version__
from project_app.app_settings import orchard

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(version: Optional[bool] = typer.Option(None,"--version","-v",
                                                help="Show the application's version and exit.",
                                                callback=_version_callback,is_eager=True,)) -> None:
    return None


@app.command()
def genetic(iter_no_progress: int = typer.Option(...,"--iter_no_progress"), max_iter: int = typer.Option(...,"--max_iter"),
            replacement_rate: float = typer.Option(...,"--replacement_rate"),
            mutation_proba: float = typer.Option(...,"--mutation_proba"),
            random_demand_rate: bool = typer.Option(False,"--random_demand_rate"),
            verbose: bool = typer.Option(False,"--verbose")) -> None:

    sol, profit, iterations = orchard.genetic_algorithm(max_iter_no_progress=iter_no_progress, max_iter=max_iter,
                                            replacement_rate=replacement_rate,
                                            mutation_proba=mutation_proba, random_demand_rate=random_demand_rate, verbose=verbose)

    results = f"{orchard.format_solution(sol)}Zysk: {profit}\nIteracje: {iterations}"
    print(results)

    with open("wyniki/algorytm_genetyczny.txt", "w") as f:
        f.write(results)


@app.command()
def annealing(t_start: int = typer.Option(..., "--t_start"),
                t_stop: int = typer.Option(..., "--t_stop"),
                iter_in_temp: int = typer.Option(..., "--iter_in_temp"),
                epsilon: int = typer.Option(..., "--epsilon"),
                iter_epsilon: int = typer.Option(..., "--iter_epsilon"),
                alpha: float = typer.Option(..., "--alpha"),
                neighbour_type: int = typer.Option(..., "--neighbour_type", min=1, max=2),
                initial_sol: int = typer.Option(..., "--initial_sol"),
                verbose: bool = typer.Option(False,"--verbose")) -> None:

    population = orchard.create_initial_population()
    if not 0 <= initial_sol < len(population):
        typer.echo(f"Numer początkowego rozwiązania musi być z przedziału 0-{len(population)-1}")
    else:
        sol, profit, _, _ = orchard.simulated_annealing(T_start=t_start, T_stop=t_stop, iterations_in_temp=iter_in_temp,
                                                        epsilon=epsilon, iterations_epsilon=iter_epsilon, alpha=alpha,
                                                        neighbour_type=neighbour_type, initial_sol=initial_sol, verbose=verbose)

        results = f"{orchard.format_solution(sol)}Zysk: {profit}"
        print(results)

        with open("wyniki/algorytm_wyrzarzania.txt", "w") as f:
            f.write(results)
