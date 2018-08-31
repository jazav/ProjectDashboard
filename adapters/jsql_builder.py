from adapters.query_builder import AbstractQueryBuilder
import logging


class JSQLBuilder(AbstractQueryBuilder):

    def get_query_str(self, x):
        return {
            'DEVPLAN': '"RnD labels" in (DevPlan, devplan, DEVPLAN)',
            'CRM': 'project in (BSS_CRM, BSS_CAM, BSS_CPM, BSS_CCM) or project = "RnD BSS Box" and component in ("Searching and DataMarts", Loyalty)',
            'ORDERING': 'project in (BSS_ORDERING) or project = "RnD BSS Box" and component in (Inventory, InventoryGAP,Marketplace, "Marketplace CORE") or project = CRAB-CRAB and component in (CRAB_AKKA)',
            'PRM': 'project in (BSS_PRM, BSS_RSS, BSS_ITC)',
            'BILLING': 'project in (BSS_GUS, BSS_BFAM, BSS_UFM, GUS) or project = "RnD BSS Box"  and component in (Payments) or project = BSS_PAY and component in (Payments)',
            'DFE': 'project in (BSS_CRMP, UIKIT, BSS_SCP, BSS_DAPI) or project = "RnD BSS Box" and component in ("Admin UI", "CSR Portal", Common)',
            'NWM': 'project in (NWM, NWM_PCRF, PCCM, NWM_AAA, NWM_NMS, NWM_OCS, NWM_UDR) or project = "RnD BSS Box" and component in (NWM)',
            'INFRA': 'project = BSS_INFRA or (project = SSO and component = "Security") or (project = CNC and component = Notification) or project = "RnD BSS Box" and component in (Notification, "Report Engine", Security)',
            'PSC': 'project = PSC-PSC and component = PSC or project = "RnD BSS Box" and component in (PSC, "Ref. Data", RefData)',
            'QC': 'project = "R&D_QС" ',
            'ARCH': 'project =  "BSS Box ARBA" and component = Architecture',
            'BA': 'project =  "BSS Box ARBA" and component in (Analytics, DFE, Billing, Infra, "Product, Resource Instances & OMS")',
            'DOC': 'project = RNDDOC',
            'IOT_CMP': 'project in (IOT_CMP, IOT_CMP_MEGAFON_GF, IOT_CMP_ROSTELECOM)',
            'IOT_AEP': 'project = IOT_AEP or project = "RnD BSS Box" and component = AEP',
            None: None
        }[x]


def test_builder():
    logging.basicConfig(filename='../../log/test.log', level=logging.INFO, format='%(asctime)s %(message)s',
                        filemode='w')

    builder = JSQLBuilder()
    q_s = builder.build('CRM') + ' or ' + builder.build('ORDERING') + ' or ' + builder.build(
        'PRM') + ' or ' + builder.build('BILLING') + ' or ' + builder.build('DFE') + ' or ' + builder.build(
        'NWM') + ' or ' + builder.build('INFRA') + ' or ' + builder.build('PSC') + ' or ' + builder.build(
        'QC') + ' or ' + builder.build('ARCH') + ' or ' + builder.build('QC')

    logging.info(q_s)
    # assert dylib_info('completely/invalid') is None


if __name__ == '__main__':
    test_builder()
