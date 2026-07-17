from prompts.workflows import configure_sc4s_prompt


def prompt_text() -> str:
    return "\n".join(message.content.text for message in configure_sc4s_prompt())


def test_configure_prompt_collects_inputs_one_at_a_time():
    text = prompt_text()

    assert "Ask one question at a time" in text
    for field in (
        "HEC URL",
        "HEC token",
        "TLS",
        "protocol",
        "hardware profile",
        "expected EPS",
        "UDP",
        "TCP",
        "disk buffer",
        "timezone",
    ):
        assert field.lower() in text.lower()


def test_configure_prompt_keeps_hardware_tuning_in_script():
    text = prompt_text()

    assert "Do not calculate hardware tuning values yourself" in text
    assert "configuration-tool.sh" in text


def test_configure_prompt_uses_tool_parameter_names():
    text = prompt_text()

    for parameter in (
        "adjust_fetch_limit",
        "udp_fetch_limit",
        "adjust_listen_sockets",
        "udp_listen_sockets",
        "udp_receive_buffer",
        "ebpf_enabled",
        "udp_input_window_enabled",
        "tcp_receive_buffer",
        "parallelize_enabled",
        "tcp_input_window_enabled",
        "adjust_disk_buffer",
        "disk_buffer_enabled",
        "timezone",
    ):
        assert f"`{parameter}`" in text


def test_configure_prompt_requires_confirmation_before_generation():
    text = prompt_text()

    confirmation = text.index(
        "Obtain explicit confirmation before calling `sc4s_build_config`"
    )
    call = text.index("Call `sc4s_build_config`", confirmation)
    assert confirmation < call


def test_configure_prompt_displays_unredacted_script_output_and_warnings():
    text = prompt_text()

    assert "display the complete unredacted `config`" in text
    assert "explain every warning" in text
    assert "generation does not change the running instance" in text


def test_configure_prompt_orders_live_application_safety_gates():
    text = prompt_text()

    generated = text.index("display the complete unredacted `config`")
    opt_in = text.index("ask whether to apply", generated)
    current = text.index("Call `get_env`", opt_in)
    strategy = text.index("merge or replace", current)
    preview = text.index("exact final `env_file`", strategy)
    confirmation = text.index(
        "explicit confirmation immediately before calling `set_env`", preview
    )
    mutation = text.index("Call `set_env`", confirmation)
    polling = text.index("Call `get_job_status`", mutation)

    assert generated < opt_in < current < strategy < preview
    assert preview < confirmation < mutation < polling


def test_configure_prompt_defines_live_application_failure_paths():
    text = prompt_text()

    for requirement in (
        "declines",
        "`get_env` fails",
        "replace removes",
        "`409 conflict`",
        "fresh confirmation",
        "rollback",
        "success",
        "failed",
        "job ID",
    ):
        assert requirement in text
