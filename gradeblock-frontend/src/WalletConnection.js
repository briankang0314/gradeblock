import React, { useState } from 'react';
import { TezosToolkit } from '@taquito/taquito';
import { BeaconWallet } from '@taquito/beacon-wallet';

const tezos = new TezosToolkit('https://mainnet.api.tez.ie');

const WalletConnection = () => {
  const [wallet, setWallet] = useState(null);
  const [userAddress, setUserAddress] = useState(null);

  const connectWallet = async () => {
    try {
      const wallet = new BeaconWallet({ name: 'GradeBlock' });
      await wallet.requestPermissions({ network: { type: 'mainnet' } });
      const userAddress = await wallet.getPKH();
      
      setWallet(wallet);
      setUserAddress(userAddress);
      tezos.setWalletProvider(wallet);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      {userAddress ? (
        <p>Wallet Connected: {userAddress}</p>
      ) : (
        <button onClick={connectWallet}>Connect Wallet</button>
      )}
    </div>
  );
};

export default WalletConnection;
