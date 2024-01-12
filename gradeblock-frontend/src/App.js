import React from 'react';
import WalletConnection from './WalletConnection';
import ContractInteraction from './ContractInteraction';
import AcademicRecordDisplay from './AcademicRecordDisplay';
import RecordUpdateProposal from './RecordUpdateProposal';
import MultisigApproval from './MultisigApproval';
import OwnershipTransfer from './OwnershipTransfer';
import RecordIntegrityVerification from './RecordIntegrityVerification';
import WalletManager from './WalletManager';
import { TezosToolkit } from '@taquito/taquito';

const tezos = new TezosToolkit('https://mainnet.api.tez.ie');

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>GradeBlock Frontend</h1>
        <WalletConnection tezos={tezos} />
        <ContractInteraction tezos={tezos} />
        <AcademicRecordDisplay tezos={tezos} contractAddress="KT1..." /> {/* Replace with your contract address */}
        <RecordUpdateProposal tezos={tezos} contractAddress="KT1..." /> {/* Replace with your contract address */}
        <MultisigApproval tezos={tezos} contractAddress="KT1..." /> {/* Replace with your contract address */}
        <OwnershipTransfer tezos={tezos} contractAddress="KT1..." /> {/* Replace with your contract address */}
        <RecordIntegrityVerification tezos={tezos} contractAddress="KT1..." /> {/* Replace with your contract address */}
        <RecordIntegrityVerification tezos={tezos} contractAddress="KT1..." /> {/* Replace with your contract address */}
      </header>
    </div>
  );
}

export default App;
