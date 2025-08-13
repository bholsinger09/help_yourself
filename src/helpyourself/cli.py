import click

@click.command()
def main():
    """Simple CLI entrypoint."""
    click.echo("Hello from help_yourself!")

if __name__ == "__main__":
    main()
