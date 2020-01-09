// Copyright (C) 2009 Red Hat, Inc.
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

package net.sourceforge.jnlp.services;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.LinkedList;
import java.util.List;

import javax.jnlp.SingleInstanceListener;
import javax.management.InstanceAlreadyExistsException;

import net.sourceforge.jnlp.JNLPFile;
import net.sourceforge.jnlp.runtime.JNLPRuntime;

/**
 * This class implements SingleInstanceService
 *
 * @author <a href="mailto:omajid@redhat.com">Omair Majid</a>
 */
public class XSingleInstanceService implements ExtendedSingleInstanceService {

    boolean initialized = false;
    List<SingleInstanceListener> listeners = new LinkedList<SingleInstanceListener>();

    /**
     * Implements a server that listens for arguments from new instances of this
     * application
     *
     */
    class SingleInstanceServer implements Runnable {

        SingleInstanceLock lockFile = null;

        public SingleInstanceServer(SingleInstanceLock lockFile) {
            this.lockFile = lockFile;
        }

        public void run() {
            ServerSocket listeningSocket = null;
            try {
                listeningSocket = new ServerSocket(0);
                lockFile.createWithPort(listeningSocket.getLocalPort());

                if (JNLPRuntime.isDebug()) {
                    System.out.println("Starting SingleInstanceServer on port" + listeningSocket);
                }

                while (true) {
                    try {
                        Socket communicationSocket = listeningSocket.accept();
                        ObjectInputStream ois = new ObjectInputStream(communicationSocket
                                .getInputStream());
                        String[] arguments = (String[]) ois.readObject();
                        notifySingleInstanceListeners(arguments);
                    } catch (Exception exception) {
                        // not much to do here...
                        exception.printStackTrace();
                    }

                }
            } catch (IOException e) {
                e.printStackTrace();
            } finally {
                if (listeningSocket != null) {
                    try {
                        listeningSocket.close();
                    } catch (IOException e) {
                        // Give up.
                        e.printStackTrace();
                    }
                }
            }
        }
    }

    /**
     * Create a new XSingleInstanceService
     */
    protected XSingleInstanceService() {
    }

    /**
     * Initialize the new SingleInstanceService
     *
     * @throws InstanceAlreadyExistsException if the instance already exists
     */
    public void initializeSingleInstance() {
        if (!initialized) {
            // this is called after the application has started. so safe to use
            // JNLPRuntime.getApplication()
            checkSingleInstanceRunning(JNLPRuntime.getApplication().getJNLPFile());
            initialized = true;
            SingleInstanceLock lockFile;
            JNLPFile jnlpFile = JNLPRuntime.getApplication().getJNLPFile();
            lockFile = new SingleInstanceLock(jnlpFile);
            if (!lockFile.isValid()) {
                startListeningServer(lockFile);
            }
        }

    }

    /**
     * Check if another instance of this application is already running
     *
     * @param jnlpFile The {@link JNLPFile} that specifies the application
     *
     * @throws InstanceExistsException if an instance of this application
     *         already exists
     */
    public void checkSingleInstanceRunning(JNLPFile jnlpFile) {
        SingleInstanceLock lockFile = new SingleInstanceLock(jnlpFile);
        if (lockFile.isValid()) {
            int port = lockFile.getPort();
            if (JNLPRuntime.isDebug()) {
                System.out.println("Lock file is valid (port=" + port + "). Exiting.");
            }
            try {
                sendProgramArgumentsToExistingApplication(port, jnlpFile.getApplication()
                        .getArguments());
                throw new InstanceExistsException(String.valueOf(port));
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

    /**
     * Start the listening server to accept arguments from new instances of
     * applications
     *
     * @param lockFile
     *            the {@link SingleInstanceLock} that the server should use
     */
    private void startListeningServer(SingleInstanceLock lockFile) {
        SingleInstanceServer server = new SingleInstanceServer(lockFile);
        Thread serverThread = new Thread(server);
        /*
         * mark as daemon so the JVM can shutdown if the server is the only
         * thread running
         */
        serverThread.setDaemon(true);
        serverThread.start();
    }

    /**
     * Send the arguments for this application to the main instance
     *
     * @param port the port at which the SingleInstanceServer is listening at
     * @param arguments the new arguments
     * @throws IOException on any io exception
     */
    private void sendProgramArgumentsToExistingApplication(int port, String[] arguments)
            throws IOException {
        try {
            Socket serverCommunicationSocket = new Socket((String) null, port);
            ObjectOutputStream argumentStream = new ObjectOutputStream(serverCommunicationSocket
                    .getOutputStream());
            argumentStream.writeObject(arguments);
            argumentStream.close();
            serverCommunicationSocket.close();

        } catch (UnknownHostException unknownHost) {
            if (JNLPRuntime.isDebug()) {
                System.out.println("Unable to find localhost");
            }
            throw new RuntimeException(unknownHost);
        }
    }

    /**
     * Notify any SingleInstanceListener with new arguments
     *
     * @param arguments the new arguments to the application
     */
    private void notifySingleInstanceListeners(String[] arguments) {
        for (SingleInstanceListener listener : listeners) {
            // TODO this proxy is privileged. should i worry about security in
            // methods being called?
            listener.newActivation(arguments);
        }
    }

    /**
     * Add the specified SingleInstanceListener
     *
     * @throws InstanceExistsException, which is likely to terminate the
     *         application but not guaranteed to
     */
    public void addSingleInstanceListener(SingleInstanceListener sil) {
        initializeSingleInstance();

        if (sil == null) {
            return;
        }

        listeners.add(sil);
    }

    /**
     * Remove the specified SingleInstanceListener
     *
     * @throws InstanceExistsException if an instance of this single instance
     *         application already exists
     *
     */
    public void removeSingleInstanceListener(SingleInstanceListener sil) {
        initializeSingleInstance();

        if (sil == null) {
            return;
        }

        listeners.remove(sil);
    }

}
