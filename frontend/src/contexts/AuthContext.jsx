import { createContext, useEffect, useMemo, useState } from 'react';
import { browserLocalPersistence, createUserWithEmailAndPassword, onAuthStateChanged, sendPasswordResetEmail, setPersistence, signInWithEmailAndPassword, signOut, updateProfile } from 'firebase/auth';
import { doc, getDoc, serverTimestamp, setDoc } from 'firebase/firestore';
import { getFirebaseAuth, getFirebaseDb } from '../services/firebase';
import { FIRESTORE_COLLECTIONS, ROLES } from '../utils/constants';

export const AuthContext = createContext(null);

const auth = getFirebaseAuth();
const db = getFirebaseDb();

async function readProfile(uid) {
  const snapshot = await getDoc(doc(db, FIRESTORE_COLLECTIONS.USERS, uid));
  return snapshot.exists() ? { id: snapshot.id, ...snapshot.data() } : null;
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let unsubscribed = false;

    setPersistence(auth, browserLocalPersistence).catch(() => undefined);

    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (!firebaseUser) {
        if (!unsubscribed) {
          setCurrentUser(null);
          setLoading(false);
        }
        return;
      }

      const profile = await readProfile(firebaseUser.uid);
      const user = {
        uid: firebaseUser.uid,
        email: firebaseUser.email ?? profile?.email ?? '',
        name: profile?.name ?? firebaseUser.displayName ?? '',
        role: profile?.role ?? ROLES.PATIENT,
        ...profile,
      };

      if (!unsubscribed) {
        setCurrentUser(user);
        setLoading(false);
      }
    });

    return () => {
      unsubscribed = true;
      unsubscribe();
    };
  }, []);

  async function register({ name, email, password, role }) {
    const credential = await createUserWithEmailAndPassword(auth, email, password);

    await updateProfile(credential.user, { displayName: name });

    const profile = {
      name,
      email,
      role,
      createdAt: serverTimestamp(),
    };

    await setDoc(doc(db, FIRESTORE_COLLECTIONS.USERS, credential.user.uid), profile, { merge: true });

    setCurrentUser({ uid: credential.user.uid, ...profile });
    return credential.user;
  }

  async function login(email, password) {
    const credential = await signInWithEmailAndPassword(auth, email, password);
    const profile = await readProfile(credential.user.uid);

    setCurrentUser({
      uid: credential.user.uid,
      email: credential.user.email ?? profile?.email ?? email,
      name: profile?.name ?? credential.user.displayName ?? '',
      role: profile?.role ?? ROLES.PATIENT,
      ...profile,
    });

    return credential.user;
  }

  async function logout() {
    await signOut(auth);
    setCurrentUser(null);
  }

  async function resetPassword(email) {
    await sendPasswordResetEmail(auth, email);
  }

  const value = useMemo(
    () => ({
      currentUser,
      loading,
      isAuthenticated: Boolean(currentUser),
      login,
      logout,
      register,
      resetPassword,
      setCurrentUser,
    }),
    [currentUser, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
