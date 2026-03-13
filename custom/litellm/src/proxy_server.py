from litellm_app import configure_proxy, run


app = configure_proxy()


if __name__ == "__main__":
    run()
