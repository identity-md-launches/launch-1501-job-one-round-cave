"""Read-only cross-provider and offline integration trials for Gathering 14."""
import importlib.util
import json
from pathlib import Path
from try_round14 import command, OUT, ROOT


def main():
    capture=json.loads((OUT/'current-zto-publicnode.json').read_text())
    start,end=capture['from_block'],capture['to_block']
    other=command('current-zto-drpc',[
        'line-4/tools/erc20-transfer-window/transfer_window.py','--rpc','https://eth.drpc.org',
        '--from-block',str(start),'--to-block',str(end)])
    if other:
        spec=importlib.util.spec_from_file_location('crosscheck',ROOT/'line-4/tools/transfer-crosscheck/crosscheck.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        agreement=module.compare(capture,other)
        (OUT/'current-zto-agreement.json').write_text(json.dumps(agreement,indent=2)+'\n')
        command('current-zto-stitch',[
            'line-4/tools/transfer-window-stitch/stitch.py', '--left',str((OUT/'current-zto-publicnode.json').relative_to(ROOT)),
            '--right',str((OUT/'current-zto-drpc.json').relative_to(ROOT))])
    command('fresh-snapshot-seal',['line-1/tools/snapshot-seal/snapshot_seal.py','seal',str((OUT/'pinned-zto-supply.json').relative_to(ROOT))])
    command('fresh-snapshot-verify',['line-1/tools/snapshot-seal/snapshot_seal.py','verify',str((OUT/'pinned-zto-supply.json').relative_to(ROOT)),str((OUT/'fresh-snapshot-seal.json').relative_to(ROOT))])
    confirmations=[]
    for name in ['current-zto-publicnode','current-zto-drpc','historical-zto-drpc']:
        p=OUT/(name+'.json')
        if not p.exists():continue
        data=json.loads(p.read_text())
        for key in ['from_block','to_block']:
            number=data[key]; returned=data[key+'_anchor']['number']
            assert number==returned
            confirmations.append({'capture':name,'requested_decimal':number,'generated_rpc_hex':hex(number),'returned_decimal':returned})
    data=json.loads((OUT/'pinned-zto-supply.json').read_text())
    number=int(data['block']['number'],16)
    confirmations.append({'capture':'pinned-zto-supply','returned_rpc_hex':data['block']['number'],'returned_decimal':number})
    (OUT/'block-number-confirmations.json').write_text(json.dumps(confirmations,indent=2)+'\n')
    command('shared-stitch-demo',['shared/stitch-handoff/stitch_handoff.py','demo'])
    command('shared-stitch-check',['shared/stitch-handoff/stitch_handoff.py','check','shared/stitch-handoff/examples/zto-stitch.zip'])


if __name__=='__main__':main()
