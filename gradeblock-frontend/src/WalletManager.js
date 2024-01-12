import React, { useState, useEffect } from 'react';
import { BeaconWallet } from '@taquito/beacon-wallet';
import { TezosToolkit } from '@taquito/taquito';

const WalletManager = ({ tezos }) => {
  const [wallet, setWallet] = useState(null);
  const [userAddress, setUserAddress] = useState('');
  const [balance, setBalance] = useState('0');

  useEffect(() => {
    if (userAddress) {
      fetchBalance();
    }
  }, [userAddress]);

  const connectWallet = async () => {
    try {
      const wallet = new BeaconWallet({ name: 'GradeBlock' });
      await wallet.requestPermissions({ network: { type: 'mainnet' } });
      const userAddress = await wallet.getPKH();
      setWallet(wallet);
      setUserAddress(userAddress);
      tezos.setWalletProvider(wallet);
    } catch (error) {
      console.error('Wallet connection failed:', error);
    }
  };

  const disconnectWallet = () => {
    setWallet(null);
    setUserAddress('');
    setBalance('0');
  };

  const fetchBalance = async () => {
    try {
      const balance = await tezos.tz.getBalance(userAddress);
      setBalance(balance.toNumber() / 1000000); // Convert from mutez to tez
    } catch (error) {
      console.error('Failed to fetch balance:', error);
    }
  };

  return (
    <div>
      <h3>Wallet Manager</h3>
      {userAddress ? (
        <div>
          <p>Address: {userAddress}</p>
          <p>Balance: {balance} XTZ</p>
          <button onClick={disconnectWallet}>Disconnect Wallet</button>
        </div>
      ) : (
        <button onClick={connectWallet}>Connect Wallet</button>
      )}
    </div>
  );
};

export default WalletManager;
