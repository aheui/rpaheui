import pytest
from aheui.option import process_options


def test_option_filename(mocker):
    mocker.patch('os.open', return_value=0)
    mocker.patch('os.close', return_value=None)
    mocker.patch('aheui.compile.read', return_value=b'')

    assert ('', 'text', b'', '1', 'run', None, False, '-', 3, -1) == process_options(['aheui-c', '-'], {})
    assert ('', 'text', b'', '1', 'run', 'x.aheuic', False, '-', 3, -1) == process_options(['aheui-c', 'x'], {})
    assert ('', 'text', b'', '1', 'run', 'x.aheuic', False, '-', 3, -1) == process_options(['aheui-c', 'x.aheui'], {})
    assert ('', 'asm', b'', '1', 'run', 'x.aheuic', False, '-', 3, -1) == process_options(['aheui-c', 'x.aheuis'], {})
    assert ('', 'bytecode', b'', '1', 'run', None, False, '-', 3, -1) == process_options(['aheui-c', 'x.aheuic'], {})

    assert ('', 'text', b'', '1', 'run', None, False, '-', 3, -1) == process_options(['aheui-c', '-', '--output=-'], {})
    assert ('', 'text', b'', '1', 'run', None, False, 'out', 3, -1) == process_options(['aheui-c', '-', '--output=out'], {})


def test_option_cmd(mocker):
    mocker.patch('os.open', return_value=0)
    mocker.patch('os.close', return_value=None)
    mocker.patch('aheui.compile.read', return_value=b'')

    heui = '희'.encode('utf-8')
    assert (heui, 'text', heui, '1', 'run', None, False, '-', 3, -1) == process_options(['aheui-c', '-c', '희'], {})
    assert (heui, 'text', heui, '1', 'run', None, False, '-', 3, -1) == process_options(['aheui-c', '-c', '희', '--output=-'], {})
    assert (heui, 'text', heui, '1', 'run', None, False, 'out', 3, -1) == process_options(['aheui-c', '-c', '희', '--output=out'], {})
    # with pytest.raises(SystemExit):
    #     process_options(['aheui-c', '-c'], {})
    with pytest.raises(SystemExit):
        process_options(['aheui-c', '-c', '희', 'x'], {})
    assert (heui, 'text', heui, '1', 'asm', None, False, '-', 3, -1) == process_options(['aheui-c', '-c', '희', '--target=asm'], {})
    assert (heui, 'text', heui, '1', 'asm', None, False, '-', 3, -1) == process_options(['aheui-c', '-c', '희', '--target=asm', '--output=-'], {})
    assert (heui, 'text', heui, '1', 'asm', None, False, 'out', 3, -1) == process_options(['aheui-c', '-c', '희', '--target=asm', '--output=out'], {})
